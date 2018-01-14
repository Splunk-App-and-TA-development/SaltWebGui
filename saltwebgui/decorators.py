# -*- coding: utf-8 -*-
"""Placeholder for custom decorators"""
import sys
from functools import wraps
from urllib2 import URLError
from flask import abort, flash, redirect, url_for
from flask_login import current_user, logout_user
from pepper import PepperException


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def api_status(f):
    """Test api status:
    - if api is working return the connection itself;
    - if there is a session error, redirect to login;
    - if saltstack is offline, return false;
    - otherwise return error
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PepperException as error:
            if error == 'Authentication denied':
                flash('Authentication timeout', 'warning')
            else:
                flash(error, 'warning')
            logout_user()
            return redirect(url_for('frontend.login'))
        except URLError as error:
            exc_info = sys.exc_info()
            if error.errno == 111:
                flash(error, 'warning')
                return False
            else:
                raise exc_info[0], exc_info[1], exc_info[2]

    return decorated_function
