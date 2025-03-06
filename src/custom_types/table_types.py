import bisect


class TableWord:
    bbox_x: int
    bbox_y: int
    bbox_width: int
    bbox_height: int
    text: str

    def __init__(
        self,
        row,
    ):
        self.bbox_x = row["left"]
        self.bbox_y = row["top"]
        self.bbox_width = row["width"]
        self.bbox_height = row["height"]
        self.text = row["text"]

    def get_y_center(
        self,
    ):
        return self.bbox_y + (self.bbox_height / 2)

    def get_x_center(
        self,
    ):
        return self.bbox_x + (self.bbox_width / 2)

    def get_x_end(
        self,
    ):
        return self.bbox_x + self.bbox_width


class PdfTableRow:
    def __init__(
        self,
    ):
        self.words: list[TableWord] = []
        self.line_broken_words: list[list[TableWord]] = []
        self.gaps = []
        self.line_broken_gaps = []

    def add_to_words(
        self,
        word: TableWord,
    ):
        bisect.insort(
            self.words,
            word,
            key=lambda x: (
                x.bbox_x,
                x.bbox_y,
            ),
        )

    def add_line_broken_words(
        self,
        word: TableWord,
    ):
        if len(self.line_broken_words) == 0:
            self.line_broken_words.append([word])
        else:
            for row in self.line_broken_words:
                row_y_range_start = row[0].bbox_y
                row_y_range_end = row_y_range_start + row[0].bbox_height
                word_y_center = word.get_y_center()
                if row_y_range_start <= word_y_center <= row_y_range_end:
                    bisect.insort(
                        row,
                        word,
                        key=lambda x: (
                            x.bbox_x,
                            x.bbox_y,
                        ),
                    )
                    return

            self.line_broken_words.append([word])
            return

    def has_in_row_range(
        self,
        word: TableWord,
    ):
        row_y_range_start = self.words[0].bbox_y
        row_y_range_end = row_y_range_start + self.words[0].bbox_height
        word_y_center = word.get_y_center()
        if row_y_range_start <= word_y_center <= row_y_range_end:
            return True
        else:
            return False

    def get_first_and_last_gap(
        self,
        img_width: int,
    ):
        first_word = self.words[0]
        last_word = self.words[-1]
        first_gap = [
            0,
            first_word.bbox_x,
            first_word.bbox_y,
            first_word.bbox_height,
        ]
        last_gap = [
            last_word.bbox_x + last_word.bbox_width,
            img_width,
            last_word.bbox_y,
            last_word.bbox_height,
        ]
        return (
            first_gap,
            last_gap,
        )

    def get_concat_by_column(
        self,
        current_column: int,
        previous_column: int,
    ):
        column_content = ""
        for word in self.words:
            word_x_center = word.get_x_center()
            if previous_column < word_x_center < current_column:
                column_content += str(word.text) + " "

        return column_content

    def get_cell_y_range(
        self,
        current_column: int,
        previous_column: int,
    ):
        y_min = self.words[0].bbox_y
        y_max = self.words[0].bbox_y + self.words[0].bbox_height
        for word in self.words:
            word_x_center = word.get_x_center()
            if previous_column < word_x_center < current_column:
                if word.bbox_y < y_min:
                    y_min = word.bbox_y
                if word.bbox_y + word.bbox_height > y_max:
                    y_max = word.bbox_y + word.bbox_height

        return (
            y_min,
            y_max,
        )
