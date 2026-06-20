from transformers import pipeline

captioner = None

def get_captioner():
    global captioner
    if captioner is None:
        captioner = pipeline(
            "image-text-to-text",
            model="Salesforce/blip-image-captioning-base"
        )
    return captioner

def image_to_query(path):
    model = get_captioner()
    result = model(path)
    return result[0]["generated_text"]