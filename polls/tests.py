
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Preparar Firefox sense interfície gràfica
        opts = Options()
        opts.add_argument("-headless")

        cls.selenium = webdriver.Firefox(options=opts)
        cls.selenium.implicitly_wait(5)

        # Superusuari de preparació permès per l'enunciat
        User.objects.create_superuser(
            "isard",
            "isard@isardvdi.com",
            "pirineus"
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_usuari_sense_permisos(self):

        navegador = self.selenium
        base = self.live_server_url

        # PAS 1: Login com a administrador
        navegador.get(f"{base}/admin/login/")

        navegador.find_element(
            By.NAME, "username"
        ).send_keys("isard")

        navegador.find_element(
            By.NAME, "password"
        ).send_keys("pirineus")

        navegador.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        ).click()

        self.assertTrue(
            navegador.find_element(
                By.ID, "user-tools"
            ).is_displayed()
        )

        # PAS 2: Crear l'usuari amb Selenium
        navegador.get(f"{base}/admin/auth/user/add/")

        navegador.find_element(
            By.NAME, "username"
        ).send_keys("sermones")

        navegador.find_element(
            By.NAME, "password1"
        ).send_keys("EAC2_Prova_Selenium!2026")

        navegador.find_element(
            By.NAME, "password2"
        ).send_keys("EAC2_Prova_Selenium!2026")

        navegador.find_element(
            By.NAME, "_save"
        ).click()

        # PAS 3: Comprovar que apareix a la llista
        navegador.get(f"{base}/admin/auth/user/")

        usuari = navegador.find_element(
            By.LINK_TEXT, "sermones"
        )

        self.assertTrue(usuari.is_displayed())

        # PAS 4: Comprovar els permisos
        usuari.click()

        self.assertFalse(
            navegador.find_element(
                By.NAME, "is_staff"
            ).is_selected()
        )

        self.assertFalse(
            navegador.find_element(
                By.NAME, "is_superuser"
            ).is_selected()
        )

        # Comprovar que no hi ha grups ni permisos assignats
        for camp in ("groups", "user_permissions"):
            llista_dreta = navegador.find_elements(
                By.ID, f"id_{camp}_to"
            )

            if llista_dreta:
                opcions = llista_dreta[0].find_elements(
                    By.TAG_NAME, "option"
                )
                self.assertEqual(len(opcions), 0)
            else:
                selector = Select(
                    navegador.find_element(By.NAME, camp)
                )
                self.assertEqual(
                    len(selector.all_selected_options), 0
                )

        # PAS 5: Tancar la sessió d'administrador
        navegador.find_element(
            By.CSS_SELECTOR, "#logout-form button"
        ).click()

        # PAS 6: Intentar login amb sermones
        navegador.get(f"{base}/admin/login/")

        navegador.find_element(
            By.NAME, "username"
        ).send_keys("sermones")

        navegador.find_element(
            By.NAME, "password"
        ).send_keys("EAC2_Prova_Selenium!2026")

        navegador.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        ).click()

        # PAS 7: Comprovar que l'accés és denegat
        self.assertIn(
            "/admin/login/",
            navegador.current_url
        )

        error = navegador.find_element(
            By.CLASS_NAME, "errornote"
        )

        self.assertTrue(error.is_displayed())

        print(
            "OK: sermones existeix, no té permisos "
            "i no pot accedir al Django Admin"
        )
