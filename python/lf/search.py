import logging, vim
from .text import Text
from .utils import vimeval

logger = logging.getLogger()

class RegexSearch(object):
    def __init__(self, text, search_panel):
        self.text = text
        self.search_panel = search_panel
        self.middle_panel = search_panel.middle

    def _pattern(self):
        return self.search_panel.cmd

    def filter(self):
        path_list = []
        pos_list = []
        logger.info('try to match pattern "{}"'.format(self._pattern()))
        try:
            for line in self.text:
                raw_text = line.raw_text
                col, length = self._match(raw_text)
                if col != -1:
                    path_list.append(line.path)
                    pos_list.append((col, length))
        except vim.error as e:
            logger.warning(e)
        self.middle_panel.path_list = path_list
        return Text(self.middle_panel), pos_list

    def _match(self, path):
        result = vimeval("matchstrpos('{}', '{}')".format(path, self._pattern()))
        start = int(result[1])
        end = int(result[2])
        length = end - start + 1
        return start, length
