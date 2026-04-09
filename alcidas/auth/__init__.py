"""ALCIDAS license auth service.

Validates license keys against Stripe subscription status.
Runs as a separate lightweight process (not part of the gateway).

Entry point: python -m alcidas.auth.server
"""
