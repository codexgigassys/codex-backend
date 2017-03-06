import pytest
import subprocess
import re


class TestHealth():

    def call_with_output(self, array):
        p = subprocess.Popen(array, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, err = p.communicate()
        return output

    def test_embed(self):
        '''
        Check if someone forgot an embed in the code
        '''
        output = self.call_with_output(
            ["find", ".", "-type", "f", "-name", "*.py",
             "-exec", "grep", "-H", "embed(" + ")", "{}", ";"])
        assert len(
            output.split()
        ) == 0, (
            'Should be zero. (Did you forget an embed?)\n'
            + "find output=\n" + str(output))

    def test_pep8(self):
        output = self.call_with_output(
            ["find", ".", "-type", "f", "-name", "*.py",
             "-exec", "pycodestyle", "-q", "{}", ";"])
        output = output.split()
        result = []
        for line in output:
            m = re.search('(/yara/|/pescanner.py)', line)
            if not m:  # we don't want to check PEP8 on migrations.
                result.append(line)

        assert len(
            result
        ) == 0, 'Should be zero. (PEP8 test failed)\n' + str(result)
