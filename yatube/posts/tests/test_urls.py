from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.user)

        group = Group.objects.create(
            title='Тестовая Группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=group,
        )

    def test_post_detail_url_exists_at_desired_location(self):
        """проверка доступности страниц любому пользователю."""
        url_names = [
            '/',
            '/group/test-slug/',
            '/profile/HasNoName/',
            '/posts/1/',
        ]

        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """проверка доступности страниц авторизованному пользователю тоже."""
        url_names = [
            '/',
            '/group/test-slug/',
            '/posts/1/',
            '/profile/HasNoName/',
            '/create/',

        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_exists_for_author(self):
        """проверка доступности страниц только автору."""
        url_names = [
            '/posts/1/edit',
        ]

        for url in url_names:
            with self.subTest(url=url):
                post_user = get_object_or_404(User, username='HasNoName')
                if post_user == self.authorized_client:
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/HasNoName/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/posts/1/edit/',
            'posts/create_post.html': 'posts/create_post.html',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
