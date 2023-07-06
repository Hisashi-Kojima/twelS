# -*- coding: utf-8 -*-
"""module for debugging
"""

import os
import subprocess


if __name__ == '__main__':
    os.chdir('../web_crawler')
    command = ['scrapy', 'list']
    subprocess.run(command, check=True)
