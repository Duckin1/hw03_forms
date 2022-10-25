from django.db import models
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slugs',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.post = PostModelTest.post
        self.post_str = str(self.post)
        self.assertEqual(len(self.post_str), 15)

        self.group = PostModelTest.group
        self.group_str = str(self.group)
        self.assertEqual((self.group_str), self.group.title)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
            """help_text в полях совпадает с ожидаемым."""
            post = PostModelTest.post
            field_help_texts = {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
            }
            for field, expected_value in field_help_texts.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        post._meta.get_field(field).help_text, expected_value)
