#!/usr/bin/env python3
# https: // github.com/MasterOdin/nullsmtpd.git
"""A noddy fake smtp server."""

import smtpd
import asyncore
import logging
import os
import sys
import argparse
import os
import time

from aiosmtpd.controller import Controller

"""
Metadata about the project
"""

__author__ = 'Robert Rottermann based on work from Matthew Peveler'
__version__ = '0.1.0'
__license__ = 'Unlicense (Public Domain)'

SMTP_PORT = 25
SMTP_FALLBACK_PORT = 2525

class FakeSMTPServer(smtpd.SMTPServer):
    """A Fake smtp server"""

    def __init__(*args, **kwargs):
        print("Running fake smtp server on port 25")
        smtpd.SMTPServer.__init__(*args, **kwargs)

    def process_message(*args, **kwargs):
        pass


"""
Logger module for NullSMTP
"""

LOGGER_NAME = 'nullsmtpd'


# pylint: disable=too-few-public-methods
class InfoFilter(logging.Filter):
    """
    Filter for logging which only allows DEBUG and INFO to go through. We use this
    to allow us to best split the logging where WARN and above are on sys.stderr and
    INFO and below are on sys.stdout.
    """
    def filter(self, record):
        return record.levelno in (logging.DEBUG, logging.INFO)


def configure_logging(mail_dir, console_logging=False):
    """
    :param mail_dir:
    :param console_logging:
    :return:
    """

    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    file_logger = logging.FileHandler(os.path.join(mail_dir, 'nullsmtpd.log'))
    file_logger.setLevel(logging.ERROR)

    info_format = "%(asctime)s [%(levelname)-7.7s] %(message)s"

    file_logger.setLevel(logging.INFO)
    log_format = logging.Formatter(fmt=info_format, datefmt="%Y-%m-%d %H:%M:%S")
    file_logger.setFormatter(log_format)

    if console_logging:
        stdout = logging.StreamHandler(sys.stdout)
        stdout.addFilter(InfoFilter())
        stdout.setLevel(logging.INFO)

        stderr = logging.StreamHandler(sys.stderr)
        stderr.setLevel(logging.WARNING)

        stdout.setFormatter(log_format)
        stderr.setFormatter(log_format)

        logger.addHandler(stderr)
        logger.addHandler(stdout)

    return logger


def get_logger():
    """
    Shortcut method to get the logger for our application
    :return:
    """
    return logging.getLogger(LOGGER_NAME)


"""
NullSMTPD module that allows to run a mock email server that just logs all incoming emails to a file
instead of actually trying to send them. Helps for developing applications that utilize email,
without spamming customers' emails and not having overhead from some GUI program.
"""

NULLSMTPD_DIRECTORY = os.path.join(os.path.expanduser("~"), ".nullsmtpd")


# pylint: disable=too-few-public-methods
class NullSMTPDHandler(object):
    """
    Handler for aiosmtpd module. This handler upon receiving a message will write the message
    to a file (as well as potentially logging the message if output_messages is True) instead
    of actually trying to send them anywhere. Useful for development of local systems being
    built in Vagrant/Docker and that we don't have a proper domain for and we don't really
    care to real all emails via a web interface.
    """
    def __init__(self, logger, mail_dir, output_messages=True, quiet=False):
        """

        :param logger: Logger to use for the handler
        :param mail_dir: Directory to write emails to
        :param output_messages: Boolean flag on whether to output messages to the logger
        """
        self.logger = logger
        if mail_dir is None or not isinstance(mail_dir, str):
            msg = "Invalid mail_dir variable: {}".format(mail_dir)
            self.logger.error(msg)
            raise SystemExit(msg)
        elif not os.path.isdir(mail_dir):
            try:
                os.mkdir(mail_dir)
            except IOError as io_error:
                self.logger.error(str(io_error))
                raise
        self.mail_dir = mail_dir
        self.print_messages = output_messages is True
        self.logger.info("Mail Directory: {:s}".format(mail_dir))
        self._quiet = quiet

    # pylint: disable=invalid-name
    async def handle_DATA(self, _, __, envelope):
        """
        Process incoming email messages as they're received by the server. We take all messages
        and log them to a file in the directory (mailbox) pertaining to the recipient and then
        we save the file with {seconds from epoch}.{mailfrom}.msg so that the messages
        are self-organizing.

        :param _: server
        :param __: session
        :param envelope: Object containing details about the email (from, receiptents, messag)
        :return: string status code of server
        """
        # peer = session.peer
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        data = envelope.content.decode('utf-8')

        self.logger.info("Incoming mail from {:s}".format(mail_from))
        for recipient in rcpt_tos:
            self.logger.info("Mail received for {:s}".format(recipient))
            mail_file = "{:d}.{:s}.msg".format(int(time.time()), mail_from)
            mail_path = os.path.join(self.mail_dir, recipient, mail_file)
            if not os.path.isdir(os.path.join(self.mail_dir, recipient)):
                os.mkdir(os.path.join(self.mail_dir, recipient))
            with open(mail_path, 'a') as open_file:
                open_file.write(data + "\n")
            if not self._quiet:
                print('%s --> %s' % (recipient, mail_path))

            if self.print_messages:
                self.logger.info(data)
        return '250 OK'


def _parse_args():
    """
    Parse the CLI arguments for use by NullSMTPD.

    :return: namespace containing the arguments parsed from the CLI
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--fork", action="store_true", default=False,
                        help="Fork and run nullsmtpd as a daemon. This will stop printing"
                             "all log messages to stdout/stderr and all emails to stdout.")
    parser.add_argument("-H", "--host", type=str, default="localhost",
                        help="Host to listen on (defaults to localhost)")
    parser.add_argument("-P", "--port", type=int, default=SMTP_PORT,
                        help="Port to listen on (defaults to 25, fallback 2525)")
    parser.add_argument("--mail-dir", type=str, default=NULLSMTPD_DIRECTORY,
                        help="Location to write logs and emails (defaults to ~/.nullsmtpd)")
    parser.add_argument("-q", "--quiet", action="store_true", default=False)
    return parser.parse_args()

def get_controller(host, port, logger, mail_dir, output_messages, quiet):
    controller = Controller(NullSMTPDHandler(logger, mail_dir, output_messages, quiet=quiet), hostname=host,
                            port=port)
    return controller
    
def main():
    """
    Main process where we get the CLI arguments, set up our loggers and then start NullSMTP,
    either running it as a daemon (default behavior) or interactively based on a passed in flag.
    """
    args = _parse_args()
    if not os.path.isdir(args.mail_dir):
        os.mkdir(args.mail_dir)

    if args.fork:
        pid = os.fork()
        if pid is not 0:
            raise SystemExit()

    host = args.host
    port = args.port
    output_messages = True #'fork' in args and args.fork
    logger = configure_logging(args.mail_dir, output_messages)
    mail_dir = args.mail_dir
    quiet = args.quiet

    try:
        logger.info("Starting nullsmtpd {:s} on {:s}:{:d}".format(__version__, host, port))
        controller = get_controller(host, port, logger, mail_dir, output_messages, quiet)
        controller.start()
    except PermissionError:
        port = SMTP_FALLBACK_PORT
        logger.info("Starting nullsmtpd {:s} on {:s}:{:d}".format(__version__, host, port))
        controller = get_controller(host, port, logger, mail_dir, output_messages, quiet=quiet)
        controller.start()
        if output_messages:
            while 1:
                input('nullsmtpd running. Press ^C to stop server and exit.')
            raise SystemExit

    except Exception as e:
        print(str(e))
        raise
    #finally:
        #logger.info('Stopping nullsmtpd')
        #controller.stop()


if __name__ == "__main__":
    main()


if __name__ == "__mainXX__":
    try:
        smtp_server = FakeSMTPServer(('localhost', SMTP_PORT), None)
    except:
        smtp_server = FakeSMTPServer(('localhost', SMTP_FALLBACK_PORT), None)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        smtp_server.close()
