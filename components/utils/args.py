#!/usr/bin/env python

import argparse

def add_arguments_environment(a_arg_parser):
    a_arg_parser.add_argument("--env", default="", help="deploy env (which determines server location)")
    a_arg_parser.add_argument("--dc", default="qa")
    return a_arg_parser

def add_arguments_logging(a_arg_parser, a_log_level):
    a_arg_parser.add_argument("--log-format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    a_arg_parser.add_argument("--log-level", default=a_log_level)
    return a_arg_parser

def add_arguments_site(a_arg_parser):
    a_arg_parser.add_argument("--site_id", default="", help="Site Identifier")
    return a_arg_parser

def add_arguments_smartview(a_arg_parser, a_app):
    a_arg_parser.add_argument("--app"  , help="the SmartApp required", default=a_app)
    a_arg_parser.add_argument("--args" , help="""extra arguments passed to the SmartApp. String of the form "a=1&b=2&b=3".""")
    return a_arg_parser

def add_arguments_auth(a_arg_parser):
    a_arg_parser.add_argument("--jwt", default="", help="jwt")
    a_arg_parser.add_argument("--oauth_id", default="", help="oauth_id")
    a_arg_parser.add_argument("--oauth_secret", default="", help="oauth_secret")
    a_arg_parser.add_argument("--oauth_scope", default="", help="oauth_scope")
    return a_arg_parser

def add_arguments_pagination(a_arg_parser):
    a_arg_parser.add_argument("--page_limit", default="", help="the max size a result list can be prior to being split into pages.")
    a_arg_parser.add_argument("--start", help="the starting item offset for the return of results.")
    return a_arg_parser
