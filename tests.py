import re
import unittest

from logstash.handler import split_string


class SplitStringTest(unittest.TestCase):
    """Test splitting strings."""

    def test_short_string(self):
        """Test split_string with a short string."""
        s = 'short string 🦄'
        self.assertEqual([s], split_string(s, chunk_size=100))

    def test_long_string(self):
        """Test that a long string is split."""
        # A mixture of single and multibyte characters.
        long_string = (
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit.'
            '🕔🍧🐪📭🏊 🏇👇🌇🏣 🍐🔯🍯💥👯📻 🔊🕝🐓📅🎁 🎄🔪💫🌊🌱👖'
            'Лорем ипсум долор сит амет, еа атяуи волуптатум меи'
            '자유민주적 기본질서에 입각한 평화적 통일 정책을'
            '映皇細情人底害企王知作点施必学上加末。'
            '情ワロ記監イ死文コ勝31協マクル上変に友校ソヱイモ細民撃2経リつか。'
            'पहोच। दर्शाता निर्देश व्याख्या जिसे हीकम तकनीकी वास्तव असक्षम'
        )

        for chunk_size in range(64, len(long_string.encode('utf-8'))):
            strings = split_string(long_string, chunk_size=chunk_size)

            # Test that the split string contains the same data as the
            # original.
            reconstructed = ''.join(strings)
            reconstructed = reconstructed.replace('…', '')
            reconstructed = re.sub(r' \(\d+/\d+\)', '', reconstructed)
            self.assertEqual(reconstructed, long_string)

            # Test that each component is as expected.
            num_strings = len(strings)
            for i, string in enumerate(strings):
                self.assertLessEqual(len(string.encode('utf-8')), chunk_size)

                # String should start with ellipsis unless it's the first
                # string.
                if i != 0:
                    self.assertRegex(string, r'^…')

                # String should end with an ellipsis and an indication of which
                # string it is…
                regex = r'… \({}/{}\)$'.format(i + 1, num_strings)

                # …unless it's the last string, when the ellipsis shouldn't be
                # present.
                if i == num_strings - 1:
                    regex = r' \({}/{}\)$'.format(i + 1, num_strings)

                self.assertRegex(string, regex)


if __name__ == '__main__':
    unittest.main()
