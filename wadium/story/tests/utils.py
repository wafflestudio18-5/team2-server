body_example = [
        [
            {
                "type": "paragraph",
                "detail": {
                    "content": "Wadium",
                    "emphasizing": "large"
                }
            },
            {
                "type": "paragraph",
                "detail": {
                    "content": "Normal <em>hello! <strong>asdbasdnb</strong>asdbpoiahsb</em>",
                    "emphasizing": "normal"
                }
            },
            {
                "type": "image",
                "detail": {
                    "size": "normal",
                    "imgsrc": "https://wadium.shop/image/",
                    "content": "image caption"
                }
            }
        ]
    ]

def make_comment_URI(self, story_pk, comment_id=None):
    if comment_id:
        return f'/story/{pk}/comment/?id={comment_id}'
    return f'/story/{pk}/comment/'