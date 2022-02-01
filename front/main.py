# -*- coding: utf-8 -*-
"""module for debugging
made by Hisashi
"""

import os
import subprocess


if __name__ == '__main__':
    os.chdir('../wiki_crawler')
    command = ['scrapy', 'list']
    subprocess.run(command, check=True)
