#include <iostream>
#include <fstream>
#include <string.h>
#include <map>
#include <set>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <limits.h>

using namespace std;

class WordTraits
{
	private:
	char* word;
	int frequency;
	int length;

	vector <int> locations;

	public:
	WordTraits(const char* s, int location = 0) : frequency(1)
	{
		create_string(s);
		locations.push_back(location);
	}

	WordTraits() : word(NULL), frequency(0), length(0) { }

	WordTraits(const WordTraits &w)
	{
		create_string(w.word);
		frequency = w.frequency;
		locations = w.locations;
	}

	WordTraits& operator = (const WordTraits &w)
	{
		if(this != &w)
		{
			delete_string();
			create_string(w.word);
			frequency = w.frequency;
			locations = w.locations;
		}
		return *this;
	}

	WordTraits& increment_frequency(int count = 1)
	{
		frequency += count;
		return *this;
	}

	WordTraits& add_location(int location)
	{
		locations.push_back(location);
	}

	~WordTraits()
	{
		delete_string();
	}

	int getlength() { return length; }
	int getfrequency() { return frequency; }
	
	friend ostream& operator << (ostream& o, const WordTraits& w);
	friend class TextFileTraits;

	//comparison functor for words (i.e. string comparison)
	struct compare_strings
	{
		bool operator() (const WordTraits* a, const WordTraits* b)
		{
			return strcmp(a->word, b->word) < 0;
		}
	};

	//comparison functor for frequency
	struct compare_frequency
	{
		bool operator() (const WordTraits* a, const WordTraits* b)
		{
			return (a->frequency > b->frequency);
		}
	};

	private:
	void create_string(const char* s)
	{
		length = strlen(s);
		word = new char [length + 1];
		strcpy(word, s);
	}

	void delete_string()
	{
		delete [] word;
		word = NULL;
		frequency = 0;
		length = 0;
	}
};

ostream& operator << (ostream& o, const WordTraits& w)
{
	o << "[" << w.word << "," << w.frequency << "]" ;
	o << " (" ;
	int i = 0, j = w.locations.size();
	for(; i < j; ++i)
		(i == j - 1) ?
		o << w.locations[i] :
		o << w.locations[i] << "," ;

	o << ")";
	return o;
}

class TextFileTraits
{
	public:
	TextFileTraits(const char* filename);

	pair <int, int> SearchWordList(char** list, int size);

	~TextFileTraits();

	friend ostream& operator << (ostream& o, const TextFileTraits& t);

	private:
	//do not allow copy construction and assignment.
	TextFileTraits(const TextFileTraits& t);
	TextFileTraits& operator = (const TextFileTraits& t);

	set <WordTraits*, WordTraits::compare_strings> words;
	multiset <WordTraits*, WordTraits::compare_frequency> frequency;

	int wc_total, wc_distinct;

typedef multiset <WordTraits*, WordTraits::compare_frequency> :: iterator multiset_iterator;
};

TextFileTraits::TextFileTraits(const char* filename) : wc_total(0), wc_distinct(0)
{
	static char buffer[128];
	static int i = 0;
	char ch;

	ifstream datafile(filename);
	if(datafile.is_open())
	{
		while(datafile.get(ch))
		{
			switch(ch)
			{
				case '(' : case ')' : break; //ignore these characters
				case ';' :
				case ',' :
				case '.' :
				case ' ' :
				case '\n':
				if(i)
				{
					buffer[i++] = '\0';
					++wc_total;
					WordTraits w(buffer);
					set <WordTraits*, WordTraits::compare_strings> :: iterator u = words.find(&w), v = words.end();
					if(u == v)
					{
						++wc_distinct;
						WordTraits *newword = new WordTraits(buffer, wc_total);
						words.insert(newword);
						frequency.insert(newword);
					}
					else
					{
						WordTraits *existingword = *u;
						pair <multiset_iterator, multiset_iterator> range = frequency.equal_range(existingword);
						for(multiset_iterator i = range.first; i != range.second; ++i)
						{
							if(*i == existingword) { frequency.erase(i); break; }
						}
						existingword->increment_frequency(1);
						existingword->add_location(wc_total);
						frequency.insert(existingword);
					}
					i = 0;
				}
				break;
				default: buffer[i++] = tolower(ch);
			}
		}
		datafile.close();
	}
}

typedef struct
{
	int location;
	WordTraits* w;
} traits_info_t;

struct compare_traits_info_t
{
	bool operator () (const traits_info_t& a, const traits_info_t& b)
	{
		return a.location < b.location;
	}
};

bool check_for_atleast_1(int* a, int size)
{
	for(int i = 0; i < size; ++i)
		if(a[i] == 0) return false;

	return true;
}

/*
given a list of strings, this function returns the minumum sized window in the text file which contains as many strings as possible in the input
list.
*/
pair <int, int> TextFileTraits::SearchWordList(char** list, int size)
{
	vector <traits_info_t> a; //accumulate all the location information from relevant WordTraits objects.
				  //for example if query list = {"apple", "orange"} and apple's locations are {10,40,50}, oranges's locations
				  //are {20,45} then "a" will be { (10, "apple"), (20, "orange"), (40, "apple"), (45, "orange"), (50, "apple") } after
				  //sorting.
	traits_info_t t;
	set <WordTraits*, WordTraits::compare_strings> :: iterator u, v = words.end();

	pair <int, int> optimum_window(0, INT_MAX); //initialize the return value.
	int window_u, window_v;

#define CHECK_AND_SET_OPTIMUM_WINDOW do { \
	if( (a[window_v].location - a[window_u].location) < (optimum_window.second - optimum_window.first)) \
	{ \
		optimum_window.first  = a[window_u].location; \
		optimum_window.second = a[window_v].location; \
	} \
} while(0)

	unordered_map <WordTraits*, int> ht;
	int index = 0;
	int * state = new int [size];

	for(int i = 0; i < size; ++i)
	{
		WordTraits w(list[i]);
		u = words.find(&w);
		if(u != v)
		{
			//the query term exists in the map. *u is a pointer to the WordTraits object that contains the information about the
			//query term.
			t.w = *u;
			ht[t.w] = index++;
			for(int j = 0; j < (*u)->locations.size(); ++j)
			{
				t.location = (*u)->locations[j];
				a.push_back(t);
			}
		}		
		state[i] = 0;
	}

	sort(a.begin(), a.end(), compare_traits_info_t());

	window_u = 0;
	for(int i = 0; i < a.size(); ++i)
	{
		++state[ht[a[i].w]];
		if(check_for_atleast_1(state, index))
		{
			window_v = i;
			CHECK_AND_SET_OPTIMUM_WINDOW;

			//try to reduce the optimum window
			while(window_u < window_v)
			{
				--state[ht[a[window_u].w]];
				++window_u;
				if(check_for_atleast_1(state, index))
					CHECK_AND_SET_OPTIMUM_WINDOW;
				else
					break;
			}
		}
	}

	for(int k = 0; k < a.size(); ++k)
		cout << a[k].location << " " ;
	cout << endl;

	delete [] state;

	return optimum_window;
}

TextFileTraits::~TextFileTraits()
{
	set <WordTraits*, WordTraits::compare_strings> :: iterator u = words.begin(), v = words.end();

	while(u != v)
	{
		delete *u;
		++u;
	}
}

ostream& operator << (ostream& o, const TextFileTraits& t)
{
	TextFileTraits::multiset_iterator u = t.frequency.begin(), v = t.frequency.end();
	int topn = 50; //how many entries to display ?

	o << "Total words = " << t.wc_total << " Distinct words = " << t.wc_distinct << endl;

	while(u != v && topn)
	{
		if((**u).getlength() >= 1) //do we want to filter by length ?
			--topn, o << **u << endl;
		++u;
	}

	return o;
}

int main(int argc, char** argv)
{
	TextFileTraits t("test.dat");

	cout << t << endl;

	if(argc > 1)
	{
		pair <int, int> w = t.SearchWordList(&argv[1], --argc);
		cout << "Window = [" << w.first << "," << w.second << "]" << endl;
	}

	return 0;
}
