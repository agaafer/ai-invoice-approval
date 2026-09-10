using Newtonsoft.Json;
using Reliance.ImageNow.API.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Utitlities
{
    public static class ImageNowProvider
    {
        private static string Token = "";
        private static string BaseURL = "http://sr01ima-10002:8080/integrationserver/";

        private static HttpClient client = new HttpClient();
        public static string GetSession()
        {
            //Get basic auth credentials for Integration server account from secure location
            //string username = "svc-imagenow-api-stg";// ConfigurationManager.AppSettings["IntegrationUser"];
            //string password = @"W]^VrL,3:_/PesHS&""2>;j.B";// ConfigurationManager.AppSettings["IntegrationPassword"];
            string username = "svc-imagenow-api-pro";// ConfigurationManager.AppSettings["IntegrationUser"];
            string password = @"!ugudW*mVpH#rgHS6lo%ch--1Wtt88LwPWh%J__i#n@1untRnc_";// ConfigurationManager.AppSettings["IntegrationPassword"];

            //http client data persists so first we clear headers
            client.DefaultRequestHeaders.Clear();

            //add auth credentials to the Authorization header
            var byteArray = Encoding.ASCII.GetBytes(username + ":" + password);
            client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Basic", Convert.ToBase64String(byteArray));

            client.DefaultRequestHeaders.Add("X-IntegrationServer-Username", username);
            client.DefaultRequestHeaders.Add("X-IntegrationServer-Password", password);

            //Send the GET request
            HttpResponseMessage response = client.GetAsync(BaseURL + "connection").Result;

            //throws exception if remote server does not return success code
            response.EnsureSuccessStatusCode();

            //Token is retrieved from the response headers and saved globally
            Token = response.Headers.GetValues("X-IntegrationServer-Session-Hash").FirstOrDefault();

            return Token;
        }

        public static void CloseSession()
        {
            //http client data persists so first we clear headers
            client.DefaultRequestHeaders.Clear();

            //Send the DELETE request
            HttpResponseMessage response = client.DeleteAsync(BaseURL + "connection").Result;

            //throws exception if not success
            response.EnsureSuccessStatusCode();
        }

        
        public static Document GetDocument(string docID)
        {
            try
            {
                //http client data persists so first we clear headers
                client.DefaultRequestHeaders.Clear();

                //Integration API will default to returning XML if we do not 
                //specify the Accept header
                client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                //Retrieve the access token from memory and 
                //add it to the request as a custom header
                client.DefaultRequestHeaders.Add("X-IntegrationServer-Session-Hash", Token);

                string url = BaseURL + $"document/{docID}";

                //Send the GET request
                HttpResponseMessage response = client.GetAsync(url).Result;

                //throws exception if not success
                response.EnsureSuccessStatusCode();



                //Read the response text and return it
                string responseBody = response.Content.ReadAsStringAsync().Result;
                Document json = JsonConvert.DeserializeObject<Document>(responseBody);  //parse the JSON to object
                return json;

            }
            catch (Exception ex)
            {
                //Always close session on fail
                //CloseSession();

                //throw;
                return null;
            }
            //Get the document metadata
         

            
        }

        public static MemoryStream getDocumentFile(string docId, string pageId)
        {


            try
            {
                //http client data persists so first we clear headers
                client.DefaultRequestHeaders.Clear();

                //Integration API will default to returning XML if we do not 
                //specify the Accept header
                // client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                //Retrieve the access token from memory and 
                //add it to the request as a custom header
                client.DefaultRequestHeaders.Add("X-IntegrationServer-Session-Hash", Token);

                //Send the GET request
                HttpResponseMessage response = client.GetAsync(BaseURL + $"v2/document/{docId}/page/{pageId}/file").Result;

                //throws exception if not success
                response.EnsureSuccessStatusCode();

                var ms = new MemoryStream();

                response.Content.CopyToAsync(ms).Wait();

                return    ms;


            }
            catch (Exception ex)
            {
                return null;

            }
            

        }

        public static MemoryStream getDocumentForm(string formId, string documentId)
        {


            try
            {
                //http client data persists so first we clear headers
                client.DefaultRequestHeaders.Clear();

                //Integration API will default to returning XML if we do not 
                //specify the Accept header
                // client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                //Retrieve the access token from memory and 
                //add it to the request as a custom header
                client.DefaultRequestHeaders.Add("X-IntegrationServer-Session-Hash", Token);

                //Send the GET request
                HttpResponseMessage response = client.GetAsync(BaseURL + $"form/{formId}/document/{documentId}?version=1").Result;

                //throws exception if not success
                response.EnsureSuccessStatusCode();

                var ms = new MemoryStream();

                response.Content.CopyToAsync(ms).Wait();

                return ms;


            }
            catch (Exception ex)
            {
                return null;

            }


        }

    }
}
