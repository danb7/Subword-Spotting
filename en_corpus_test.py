from collections import Counter
import random
import nltk
nltk.download('brown')
nltk.download('stopwords')

from nltk.corpus import brown, stopwords

stop_words = set(stopwords.words('english'))

brown_words = brown.words()

filtered_words = [word for word in brown_words if (word.lower() not in stop_words) and (word.isalpha())]

brown_counter = Counter(filtered_words)
print(len(brown_counter.keys()))

filtered_brown_counter = {word: count for word, count in brown_counter.items() if count > 30}
print(len(filtered_brown_counter.keys()))

print(random.sample(population=filtered_brown_counter.keys(),
              counts=filtered_brown_counter.values(),
              k=10)
)