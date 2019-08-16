# Event Fundraising

An event fundraising website where individuals can create personal pages, set goals and raise money for the overall goal.

Built in Python/Django 2.2 and Bootstrap 4 for the [Triple Crown for Heart](https://triplecrownforheart.ca/) bike ride, because you shouldn't be charged for charity fundraising.

Currently used at: [https://donations.triplecrownforheart.ca/team_fundraising/](https://donations.triplecrownforheart.ca/team_fundraising/). If you would like to use this platform for your charity fundraising event, please contact the [author](#authors).

## Getting Started

### Prerequisites

* [Python 3.7](https://www.python.org/)
* [git](https://git-scm.com/)

### Installing

1. (optional) Create and activate a [virtualenv](https://virtualenv.pypa.io/) to have an isolated environment (you may want to use [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)).

2. Clone this repository:

   `git clone https://github.com/dominikszopa/fundraising.git`
   `cd fundraising`

3. Install dependencies

   `pip install -r requirements.txt`

4. Create a database

   `python3 ./manage.py migrate`

5. Load test data into the database from fixtures:

   `python3 ./manage.py loaddata`

6. If everything has gone ok, you should be able to start the Django development server:

   `python3 ./manage.py runserver localhost:8000`

7. You can browse to [http://localhost:8000/team_fundraising/](http://localhost:8000/team_fundraising/)

## Deployment

## Support

For any issues installing, using or contributing, please feel free to contact the [author](#authors).

## Built with

* [Python 3.7](https://docs.python.org/3/) - Primary language
* [Django 2.2](https://docs.djangoproject.com/en/2.2/) - Web Framework
* [django-paypal](https://django-paypal.readthedocs.io/en/stable/) - Payment processor
* [Bootstrap 4](https://getbootstrap.com/docs/4.0/getting-started/introduction/) - Interface
* [django-crispy-forms](https://django-crispy-forms.readthedocs.io/en/latest/) - Bootstrap forms
* [CKEditor 4](https://ckeditor.com/ckeditor-4) - WYSIWYG editor

## Contributing

If you belong to a charity or non-profit event that has a fundraising component and would like to use this platform for your event, the author can help you get set up. This will also help development by making the product more easily adaptable to events.

If you are a Django/Python or CSS developer, we have a healthy list of features we would like to implement in the [TODO](TODO) file. I may move that to a ticket tracker if a few people join. The author will approve pull requests for the time being. I am also looking for designer help to clean up the design and make a nicer "thermometer".

This project has adopted the [Contributor Covenant](https://www.contributor-covenant.org), version 1.4, available at [https://www.contributor-covenant.org/version/1/4/code-of-conduct.html](https://www.contributor-covenant.org/version/1/4/code-of-conduct.html)

## Authors

* **Dominik Szopa** - *Django, HTML, CSS* - [DominikSzopa](https://github.com/dominikszopa) - <techdomi@gmail.com>

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

* [Horizontal Fundraising Thermometer](https://codepen.io/robotballoon/pen/Fjnyp) by [Robot Balloon](https://codepen.io/robotballoon)
* [Simple jQuery Search Filter](https://codepen.io/alexerlandsson/pen/ZbyRoO) by [Alexander Erlandsson](https://codepen.io/alexerlandsson)
