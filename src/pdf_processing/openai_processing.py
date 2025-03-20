import base64
import io

from openai import OpenAI
from PIL import Image
from src.custom_types.api_types import SingleTableRequest
from src.custom_types.interfaces import TableExtractionInterface
from src.service.service_helper import ServiceHelper


class OpenAiProcessing(TableExtractionInterface):
    def __init__(self):
        super().__init__()
        self.client = OpenAI()
        self.helper = ServiceHelper()

    # Function to encode the image
    def __encode_image(self, table_image):
        # Convert NumPy array to PIL Image
        pil_image = Image.fromarray(table_image)
        
        # Create a bytes buffer
        buffer = io.BytesIO()
        
        # Save the image to the buffer (in PNG format)
        pil_image.save(buffer, format="PNG")
        
        # Get the bytes from the buffer and encode to base64
        img_bytes = buffer.getvalue()
        base64_encoded = base64.b64encode(img_bytes).decode("utf-8")
        
        return base64_encoded
        
    def __get_chatgpt_answer(self, base64_table_image) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Format as excel table, data are as numbers. Return table as markdown without any additional description.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_table_image}"},
                        },
                    ],
                }
            ],
        )

        answer = response.choices[0].message.content
        return answer

    def __parse_markdown_table(self, gpt_answer: str):
        replace_new_line = gpt_answer.replace('\\n', '\n')
        first_table_char_idx = replace_new_line.find('|')
        last_table_char_idx = replace_new_line.rfind('|')

        if first_table_char_idx == -1 or last_table_char_idx == -1 or first_table_char_idx == last_table_char_idx:
            print("error")

        md_table = replace_new_line[first_table_char_idx:last_table_char_idx+1]   
        lines = md_table.split('\n')
        header = lines[0].strip('|').split('|')

        table_body = []
        for line in lines[2:]:
            # Break once we hit an empty line
            if not line.strip():
                break

            cols = line.strip("|").split("|")
            table_body.append(cols)

        # merge header with table body - put it to first place in list
        # remove trailing whitespaces from words
        table_body.insert(0, header)
        for i in range(len(table_body)):
            table_body[i] = list(
                map(
                    lambda x: x.strip(),
                    table_body[i]
                )
            )
        return table_body

    def extract_tabular_data(self, rectangle_data: SingleTableRequest):
        table_image = self.helper.crop_image(rectangle_data)
        base64_image = self.__encode_image(table_image)
        gpt_answer = self.__get_chatgpt_answer(base64_image)
        result = self.__parse_markdown_table(gpt_answer)
        print("chatgpt\n", result)
        return result
