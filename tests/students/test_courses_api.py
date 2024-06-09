import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
from students.models import Course, Student


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture()
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture()
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_one_course(client, course_factory):
    create_course = course_factory(_quantity=1)
    first_course = create_course[0]
    response = client.get(f'/api/v1/courses/{first_course.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == first_course.name


@pytest.mark.django_db
def test_all_courses(client, course_factory):
    create_course = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    for i, course in enumerate(data):
        assert course['name'] == create_course[i].name


@pytest.mark.django_db
def test_id_filter(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get('/api/v1/courses/', {'id': course[0].id})
    assert response.status_code == 200
    data = response.json()
    assert course[0].id == data[0]['id']


@pytest.mark.django_db
def test_name_filter(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get('/api/v1/courses/', {'name': course[0].name})
    assert response.status_code == 200
    data = response.json()
    assert course[0].name == data[0]['name']


@pytest.mark.django_db
def test_create_course(client):
    response = client.post(reverse('courses-list'), data={
        'name': 'python'
    }, format='json')
    assert response.status_code == 201
    data = response.json()
    assert Course.objects.get(id=data['id']).name == 'python'


@pytest.mark.django_db
def test_course_change(client, course_factory):
    course = course_factory(_quantity=10)
    response = client.patch(reverse('courses-detail', args=[course[0].id]), data={
        'name': 'python'
    }, format='json')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'python'


@pytest.mark.django_db
def test_course_delete(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.delete(reverse('courses-detail', args=[course[0].id]))
    assert response.status_code == 204