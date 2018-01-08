# Task Challange

This repo consists of several endpoints to perform crud operation and using oauth password grant for authentication.

This project created using python2 and flask framework.

## Requirement
Run: 

```$ pip install -r requirements.txt ```

It will install all required dependecies.

Once all the dependencies installed you can run ```$ python app.py ``` on the terminal to start the application and the server will run at ```http://localhost:3000```. However you can change the port to your own choice on file ```config.py```.

All available endpoints is exactly the same as provided in [this website](https://jsonplaceholder.typicode.com/) .

## Guide
* First you need to generate a client, this can be achieved by visiting ```/``` route.
* Then you can create a user on the ```/users``` route using post method, e.g.:
```javascript
{
	"name": "Afdol",
	"username": "afdolriski",
	"password": "test",
	"email": "test@aja.com"
}
```

Note that all the fields above are required, the rest is optional.
* Finally, get a token on the ```/oauth/token``` route using form-data.
```javascript
{
	"client_id": "random string that has been genereated before",
	"username": "afdolriski",
	"password": "test",
	"grant_type": "password"
}
```

That's it! you can access all the available route now.

Happy ```REST```*ing* !!!

