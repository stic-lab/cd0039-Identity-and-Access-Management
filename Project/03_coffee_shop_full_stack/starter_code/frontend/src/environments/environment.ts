/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'stic-lab.us', // the auth0 domain prefix stic-lab.us.auth0.com'
    audience: 'http://127.0.0.1:3000', // the audience set for the auth0 app
    clientId: 'omU89FlxfYmwgv3b3cm9CVvYFqewjyXG', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100', // the base url of the running ionic application. 
  }
}