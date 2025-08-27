# import celery
from .celery import app as celery_app


__all__ = ['celery_app']
# To explicitly expose the Celery app object when the project is imported.
# Explicitly exposes only celery_app from the myshop package for cleaner, controlled imports.

# ----------- Explanation with example: ---------------
#  # myproject/__init__.py
#
# hammer = "I'm a hammer!"
# screwdriver = "I'm a screwdriver!"
# _internal_tool = "You shouldn't usually touch me directly."
#
# from .celery import app as celery_app
#
# __all__ = ['celery_app'] # <--- THE MAGIC LINE

# # main.py
# from myproject import *
#
# print(hammer)         # ERROR! NameError: name 'hammer' is not defined
# print(screwdriver)    # ERROR! NameError: name 'screwdriver' is not defined
# print(celery_app)     # This works!
# # print(_internal_tool) # Would also be an ERROR!

# What happens now?
#
# When you say from myproject import *, Python sees the __all__ list in myproject/__init__.py.
# It then says, "Aha! The developer has explicitly told me what to expose when * is used.
# I will only bring in the names listed in __all__."
#
# hammer is not in __all__, so it's not imported. You get an error if you try to use it directly.
#
# screwdriver is not in __all__, so it's not imported. Error.
#
# celery_app is in __all__, so it IS imported. This works perfectly.
#
# _internal_tool is not in __all__, so it's not imported. Error.