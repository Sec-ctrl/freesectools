from flask import g
import base64
import os


def add_security_headers(response):
    # Ensure g.csp_nonce is set, generate if it's missing
    nonce = getattr(g, "csp_nonce", None)
    if nonce is None:
        nonce = base64.b64encode(os.urandom(16)).decode("utf-8")
        g.csp_nonce = nonce

    # Apply other security headers globally
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )

    # Adjust the CSP to allow Google's scripts and styles
    csp = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net https://cdn.tiny.cloud "
        "https://www.googletagmanager.com https://*.googlesyndication.com; "
        "style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com "
        "'unsafe-inline' https://*.googlesyndication.com; "
        "font-src 'self' https://use.fontawesome.com; "
        "img-src 'self' https://sp.tinymce.com https://blogger.googleusercontent.com "
        "data: https://*.googlesyndication.com; "
        "frame-src 'self' https://*.googlesyndication.com; "
        "connect-src 'self' https://cdn.jsdelivr.net https://*.google-analytics.com "
        "https://*.googletagmanager.com https://*.googlesyndication.com; "
        "object-src 'none'; form-action 'self'; base-uri 'self'; "
        "upgrade-insecure-requests;"
    )

    # Apply the updated CSP header
    response.headers["Content-Security-Policy"] = csp

    return response
