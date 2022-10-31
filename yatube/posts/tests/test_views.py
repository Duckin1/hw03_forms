from django import forms
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class TaskURLTests(TestCase):
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

        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': (reverse
                ('posts:index')
            ),
            'posts/group_list.html': (reverse
                ('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                args=[get_object_or_404(User, username='HasNoName')]
            ),
            'posts/post_detail.html': (reverse
                ('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ),
            'posts/create_post.html': reverse(
                'posts:post_create'
            ),
        }
        # Проверяем, что при обращении к index вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        for post in Post.objects.select_related('group'):
            self.assertEqual(response.context.get('post'), post)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        group = get_object_or_404(Group, slug=self.group.slug)
        first_objects = group.posts.all()
        for post in first_objects:
            self.assertEqual(response.context.get('post'), post)
        second_object = response.context.get('page_obj').object_list
        for post in second_object:
            self.assertEqual(response.context.get('post'), post)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=[self.user])
        )
        author = self.user
        first_objects = author.posts.all()
        for post in first_objects:
            self.assertEqual(response.context.get('post'), post)
        second_object = response.context.get('page_obj').object_list
        for post in second_object:
            self.assertEqual(response.context.get('post'), post)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_right_group_exists(self):
        """Проверка Создания Поста и если при создание поста выбрать группу"""

        response = self.authorized_client.get(
            reverse('posts:index')
        )
        object = self.group.posts.filter(
            group=response.context.get('post').group
        )
        self.assertTrue(object.exists())
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        object = self.group.posts.filter(
            group=response.context.get('post').group
        )
        self.assertTrue(object.exists())
    def test_post_right_group(self):
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        for post in Post.objects.select_related("group"):
            self.assertEqual(response.context.get('post').group, post.group)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        object = self.group.posts.all()
        for post in object:
            self.assertEqual(response.context.get('post').group, post.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая Группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый текст{i}',
                    author=cls.user,
                    group=cls.group
                )
                for i in range(0, 13)
            ]
        )

    def test_first_page_contains(self):
        """Тест Пагинатора для Первой странцы"""
        PAGE_LIMIT = 10
        url_names = {
            reverse('posts:index'): PAGE_LIMIT,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): PAGE_LIMIT,
            reverse(
                'posts:profile',
                args=[self.user]
            ): PAGE_LIMIT,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=1')
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        """Тест Пагинатора для Второй странцы"""
        PAGE_LIMIT_SECOND_PAGE = 3
        url_names = {
            reverse(
                'posts:index'
            ): PAGE_LIMIT_SECOND_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): PAGE_LIMIT_SECOND_PAGE,
            reverse(
                'posts:profile',
                args=[self.user]
            ): PAGE_LIMIT_SECOND_PAGE,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
