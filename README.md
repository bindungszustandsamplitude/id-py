# id-py
A simple tool to retrieve the information of a ordered car at Volkswagen based on the commission number without logging into the MyVolkswagen website.

## Wait a minute. How do you manage to retrieve this data without logging in? Are you a hacker?
No, I am not. Logging into the website is boring, takes a lot of time and the certainty to read "FIN noch nicht bekannt" gets more and more depressing after time. This program _automates_ this whole process. It effectively does exactly the same that you would do, but much faster, without clicking buttons, without executing all the JavaScript code. The functionality is summarized very simple:

1. The tool gets a request for a commission number.
2. The tool tries out the last Bearer token that worked for the retrieval.
3. If the Bearer token passes the test, it will be used for retrieving the data. If it does not pass the test, a new one will be generated and stored to the embedded database.
4. The data will be retrieved by calling the VW API and displayed on the website.

No elementary particle physics here (although I actually _am_ an elementary particle physicist, he he he hm - \*starres bashfully into the corner\*), but just the automization of veeeeeery time-consuming things. I guess, the time I spent doing this tool exceeds the time I will spend in total in order to retrieve the information about my ordered car, but I hope it saves _you_ a lot of time.


## I am very interested in how the application is actually working. How can I understand that quite quickly?

I recommend two code files:
* If you are interested in the general workflow: `views.py`. Look into the function `number()` and read the comments.
* If you are interested in how a token is retrieved etc: have a look into `vwrequest.py`


## How can I use this tool without installing it on my own machine?

An instance is currently actively running on  
https://habe-ich-eine-fin.nsanto.de

Use the following endpoints:
* interactive index page: `https://<BASE_URL>`
* verbose view: `https://<BASE_URL>/<commission_number>`
* only a concise flag if a vin exists: `https://<BASE_URL>/<commission_number>/concise`


## How do I use this tool on my machine?
This tool requires Python 3 with Django:
```
python3 -m pip install django
```
Follow the following steps in order to host this tool on your own:

1. Install Python and the required packages. It might be beneficial to work with a virtual environment (venv).
1. Clone this repository.
2. Change into the directory that contains the files `setup.sh` and `manage.py`.
3. On Linux/Unix machines: execute the shell script `setup.sh`.  
On Windows machines: perform the steps of the script manually.
1. Modify the file `id_py/settings.py` for your needs. Some hints for this are given below.
2. Define environment variables with credentials for the MyVolkswagen website as follows:
   ```bash
   export VW_LOGIN_EMAIL=<email-address>
   export VW_LOGIN_PASSWORD=<password>
   export SPEC_CONFIG_LOCATION=<spec-config-location>
   ```
   Fill the fillers. Use your own credentials or just create a new account if you want to stay more "anonymous". The `<spec-config-location>` is the absolute path of your spec config file (see below).
3. Start the server by typing the command
    ```
    python3 manage.py runserver <port>
    ```
    where `<port>` is the port number you want to use.
4. Open a browser and type the following in there:
   ```
   http://localhost:<port>/<commission_number>
   ```
   `<port>` is the port, `<commission_number>` is a commission number.


## How to I set the `settings.py` properly?

* provide a unique `SECRET_KEY`.
* set the debug mode to false when you go into "production".
* when debug mode is false, provide your allowed hosts to `ALLOWED_HOSTS`, for example `localhost` for a local environment.
* use a web server such as `nginx` or `apache2` if you want to expose your application to the internet.


## How do I configure the application?

For this, feel free to modify the following files:
* `config.py`: basic configuration
* `number_template.html`: the html template of the site
* `consts.py`: modify constants such as literals used in the html template.
* create a spec config file (see below)
* the rest of the source code for special things, of course


## How do I create a spec configuration?

The spec config defines the VW specs you are viewing ("Ausstattungsmerkmale"). It's a file of new-line-separated substrings of specs. One example for the spec file is the following:
```
assistenzpaket
fertigungsablauf
head-up
```
It will look case-insensitively for superstrings of those entries and show the first one that is found on the website. The application does not have to restart by changing the file. As told before, you have to refer to the absolute path of you spec config by setting the environment variable `SPEC_CONFIG_LOCATION`.


## I found an issue. How can I contact you?

Two possibilities:
* Open an issue here on GitHub
* Solve the issue and create a Pull Request


## I want to buy you a coffee for your work. How can I do this?

I don't ask for this, you can use the tool for free. But if you want, you can pay my next coffee using PayPal: https://paypal.me/nsantowsky
