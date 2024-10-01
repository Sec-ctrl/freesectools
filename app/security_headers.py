from flask import g, request
import base64
import os


def add_security_headers(response):
    # Ensure g.csp_nonce is set, generate if it's missing
    nonce = getattr(g, "csp_nonce", None)
    if nonce is None:
        nonce = base64.b64encode(os.urandom(16)).decode("utf-8")
        g.csp_nonce = nonce  # Optionally set it in g for consistency
    # Apply other security headers globally
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )

    # Start with the base strict CSP
    csp = (
        f"default-src 'self'; "
        f"script-src 'self' https://cdn.jsdelivr.net https://cdn.tiny.cloud 'nonce-{g.csp_nonce}'; "
        f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com https://unpkg.com https://cdn.tiny.cloud; "
        f"font-src 'self' https://use.fontawesome.com https://cdn.tiny.cloud; "
        f"img-src 'self' https://sp.tinymce.com https://blogger.googleusercontent.com data: https://cdn.tiny.cloud; "
        f"object-src 'none'; "
        f"frame-ancestors 'none'; "
        f"form-action 'self'; "
        f"base-uri 'self'; "
        f"upgrade-insecure-requests; "
        f"connect-src 'self' https://cdn.tiny.cloud"
        f"frame-ancestors 'self';"
        f"form-action 'self';"
    )

    # For the /blogs/new page, adjust only the relevant parts of the CSP (style-src)
    if request.path == "/blogs/new" or request.path == request.path.startswith(
        "/blogs/edit/"
    ):
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://cdn.tiny.cloud 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://use.fontawesome.com https://unpkg.com https://cdn.tiny.cloud 'nonce-{g.csp_nonce}'; "  # Allow 'unsafe-inline' only here
            f"font-src 'self' https://use.fontawesome.com https://cdn.tiny.cloud; "
            f"img-src 'self' https://sp.tinymce.com https://blogger.googleusercontent.com data: https://cdn.tiny.cloud; "
            f"object-src 'none'; "
            f"frame-ancestors 'none'; "
            f"form-action 'self'; "
            f"base-uri 'self'; "
            f"upgrade-insecure-requests; "
            f"connect-src 'self' https://cdn.tiny.cloud"
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/passwordgen":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com; "
            f"img-src 'self' https://blogger.googleusercontent.com data: 'nonce-{g.csp_nonce}'; "
            f"font-src 'self' https://use.fontawesome.com; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/password-breach":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com; "
            f"img-src 'self' data: https://blogger.googleusercontent.com; "
            f"font-src 'self' https://use.fontawesome.com; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/whois":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com 'nonce-{g.csp_nonce}';"
            f"img-src 'self' data: https://blogger.googleusercontent.com; "
            f"font-src 'self' https://use.fontawesome.com; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/ip-geolocation":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://unpkg.com https://cdn.jsdelivr.net https://use.fontawesome.com 'nonce-{g.csp_nonce}'; "
            f"img-src 'self' data: https://unpkg.com *.openstreetmap.org  https://blogger.googleusercontent.com; "
            f"font-src 'self' https://use.fontawesome.com https://unpkg.com; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/ip-blacklist":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com 'nonce-{g.csp_nonce}'; "
            f"img-src 'self' data: https://blogger.googleusercontent.com; "
            f"font-src 'self' https://use.fontawesome.com https://unpkg.com; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/fingerprint":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com ; "
            f"img-src 'self' data: https://blogger.googleusercontent.com https://cdn.jsdelivr.net; "
            f"font-src 'self' https://use.fontawesome.com ; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/dns-lookup":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com ; "
            f"img-src 'self' data: https://blogger.googleusercontent.com https://cdn.jsdelivr.net; "
            f"font-src 'self' https://use.fontawesome.com ; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    elif request.path == "/":
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'nonce-{g.csp_nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com 'nonce-{g.csp_nonce}'; "
            f"img-src 'self' data: https://blogger.googleusercontent.com https://cdn.jsdelivr.net; "
            f"font-src 'self' https://use.fontawesome.com ; "
            f"connect-src 'self'; "
            f"frame-ancestors 'self';"
            f"form-action 'self';"
        )
    # Apply the CSP header
    response.headers["Content-Security-Policy"] = csp

    return response
