#!/usr/bin/env python

import argparse

def add_environment_arguments(a_arg_parser):
    a_arg_parser.add_argument("--env", default="", help="deploy env (which determines server location)")
    a_arg_parser.add_argument("--dc", default="qa")
    return a_arg_parser

def add_logging_arguments(a_arg_parser, a_log_level):
    a_arg_parser.add_argument("--log-format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    a_arg_parser.add_argument("--log-level", default=a_log_level)
    return a_arg_parser

def add_site_arguments(a_arg_parser):
    a_arg_parser.add_argument("--site_id", default="", help="Site Identifier")
    return a_arg_parser

def add_token_arguments(a_arg_parser):
    a_arg_parser.add_argument("--oauth_id", default="", help="oauth-id")
    a_arg_parser.add_argument("--oauth_secret", default="", help="oauth-secret")
    a_arg_parser.add_argument("--oauth_scope", default="", help="oauth-scope")
    a_arg_parser.add_argument("--jwt", default="", help="jwt")
    return a_arg_parser

def add_smartview_arguments(a_arg_parser, a_app):
    a_arg_parser.add_argument("--app"  , help="the SmartApp required", default=a_app)
    a_arg_parser.add_argument("--start", help="""Value for start. A JSON object detailed elsewhere.""", default="""{"from":"continuous"}""")
    a_arg_parser.add_argument("--keep-alive", help="maximum interval between messages being sent", default="10s")
    a_arg_parser.add_argument("--args" , help="""extra arguments passed to the SmartApp. String of the form "a=1&b=2&b=3".""")
    return a_arg_parser
