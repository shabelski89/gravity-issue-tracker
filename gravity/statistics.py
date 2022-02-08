import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib.pyplot import figure
from gravity.utills import get_filename


def get_wordcloud_from_issues_message(text: str):
    """Make wordcloud graph to show most commented issues"""
    wordcloud = WordCloud(width=480, height=480, margin=0, background_color='white').generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')

    plt.axis("off")
    plt.margins(x=0, y=0)
    figure(figsize=(3, 4), dpi=300)
    plt.axis('off')

    filename = get_filename()
    wordcloud.to_file(filename)
    # plt.show()
    return filename
