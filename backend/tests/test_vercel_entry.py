def test_vercel_entry_exposes_the_wsgi_app():
    from index import app

    assert callable(app)
