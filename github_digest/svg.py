import base64

import requests
from cairosvg import svg2png


# https://jsfiddle.net/3kjfLog6/
# http://stylecampaign.com/blog/2014/01/basics-of-svg-in-email/
# https://stackoverflow.com/questions/37753911/how-can-i-embed-svg-into-html-in-an-email-so-that-its-visible-in-most-all-emai
def svg_url_to_base64_png(svg_url, width=32, height=32, dpi=300):
    response = requests.get(svg_url)
    response.raise_for_status()

    png_data = svg2png(
        bytestring=response.content,
        output_width=width,
        output_height=height,
    )

    return f"data:image/png;base64,{base64.b64encode(png_data).decode('utf-8')}"


if __name__ == "__main__":
    print(
        svg_url_to_base64_png(
            "https://raw.githubusercontent.com/primer/octicons/main/icons/star-16.svg",
            32,
            32,
        )
    )
