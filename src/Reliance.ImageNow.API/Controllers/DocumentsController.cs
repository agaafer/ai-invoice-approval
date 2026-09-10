using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Python.Runtime;
using Reliance.ImageNow.API.Data;
using Reliance.ImageNow.API.Models;
using Reliance.ImageNow.API.Utitlities;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class DocumentsController : ControllerBase
    {
        private readonly AppDbContext _context;
        private readonly PredictionDbContext _predictionDbContext;

        private readonly ILogger<DocumentsController> _logger;
        private readonly AppSettings _appSettings;

        public DocumentsController(ILogger<DocumentsController> logger,IOptions<AppSettings> appSettings,AppDbContext context,PredictionDbContext predictionDbContext)
        {
            _logger = logger;
            _appSettings = appSettings.Value;
            _context = context;
            _predictionDbContext = predictionDbContext;
           
        }

        [HttpGet]
        public IEnumerable<Document> Get([FromQuery] DocumentQuery documentQuery)
        {
            List<Document> documents = null;

            IQueryable<Document> queryable = _context.Documents.AsNoTracking();

            queryable = queryable.Where(p => p.DocumentTypeId == "301YV3X_0005J7FB600006G");


            if (documentQuery.startDate.HasValue)
            {
                queryable = queryable.Where(p => p.Instance.CreatedDateTime >= documentQuery.startDate);
            }
            if (documentQuery.endDate.HasValue)
            {
                queryable = queryable.Where(p => p.Instance.CreatedDateTime <= documentQuery.endDate.Value.AddDays(1));
            }
            if (!string.IsNullOrEmpty(documentQuery.queueName))
            {
                queryable = queryable.Where(p => p.Instance.WorkflowItems.Any(p => p.WorkflowQueueId == documentQuery.queueName));
            }

            // queryable = queryable.OrderBy(p => p.Instance.CreatedDateTime);
            //queryable = queryable.OrderBy(p => p.Instance.SortDate);
            documents = queryable.Include(document => document.Instance)
                .ThenInclude(instance => instance.Properties)
                .Include(document => document.Instance).ThenInclude(instance => instance.WorkflowItems).ThenInclude(workflowItem => workflowItem.WorkflowQueue).Take(1000).ToList();

            List<BatchPredection> batchPredections = _predictionDbContext.BatchPredections.AsNoTracking().ToList();

            foreach (var item in documents)
            {
                BatchPredection batchPredection = batchPredections.FirstOrDefault(p => p.DocumentId == item.Id);
                string notes = _predictionDbContext.BatchPredictionNotes.OrderByDescending(s => s.Id).FirstOrDefault(p => p.DocumentId == item.Id && p.InvoiceNumber == item.InvoiceNumber)?.Notes;
                if (batchPredection != null)
                {
                    item.Name = batchPredection.Name;
                    item.Percent = batchPredection.Percent;
                    
                }
                if (notes != string.Empty && notes != null)
                {
                    item.Notes = notes;
                }
            }

            // Sort by 
            documents = documents.OrderBy(a => a.Instance.QueueStartDateTime).ToList();
                return documents;
            


        }

        [HttpPost("AddNote")]
        public ActionResult AddNote([FromBody] NoteCommand command)
        {
            try
            {
                _predictionDbContext.BatchPredictionNotes.Add(new BatchPredictionNotes { DocumentId = command.DocumentId, InvoiceNumber = command.InvoiceNumber, Notes = command.Notes });
                _predictionDbContext.SaveChanges();
                return Ok();
            }
            catch(Exception ex) 
            { return BadRequest(); }

        }

        [HttpGet("{documentId}/prediction")]
        public PredictionResult GetFile(string documentId)
        {


            ImageNowProvider.GetSession();
            Document document = ImageNowProvider.GetDocument(documentId);
            List<string> filePaths = new List<string>();
          
            if (document != null)
            {
               

                if (document.pages.Count > 0)
                {
                    foreach (var page in document.pages)
                    {
                        // Get Document File
                        MemoryStream pageStream = null;

                        if (!string.IsNullOrEmpty(page.id))
                            pageStream = ImageNowProvider.getDocumentFile(documentId, page.id);

                        pageStream.Seek(0, SeekOrigin.Begin);

                        string filePath = Path.Combine(@"E:\Mine\ImageNowFiles\files", documentId + "_"  + page.id + ".tiff");
                        using (var fs = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None))
                        {
                            pageStream.CopyToAsync(fs).Wait();
                        }
                        filePaths.Add(filePath);
                    }
                    //if (document.pages.Count > 1)
                    //    throw new Exception("Invoice has multiple pages which is not supported for the sake of POC.");
                    
                }

            }
            

            // Get Document Forms
            MemoryStream formStream = null;

            if (document != null)
            {
                formStream= ImageNowProvider.getDocumentForm("301YV3X_0005J7FB600007J", documentId);

            }
            formStream.Seek(0, SeekOrigin.Begin);

            string formPath = Path.Combine(@"E:\Mine\ImageNowFiles\files", documentId + ".xml");
            using (var fs = new FileStream(formPath, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                formStream.CopyToAsync(fs).Wait();
            }


            try
            {


                if (!PythonEngine.IsInitialized)
                    PythonEngine.Initialize();



                using (Py.GIL()) // Ensures the Python interpreter lock
                {
                    // Import the Python module

                    dynamic predictionModule = Py.Import(_appSettings.PythonModule); // Make sure the script is in the correct location
                    

                    // Call the prediction function
                    //dynamic result = predictionModule.get_perdiction("C:\\Users\\Mohamed.Kassem\\Downloads\\sample_dir\\sample_dir\\321Z5B5_0LG6CS814008H2J_321Z5B5_0LG6CS814008H2J_1_1.png"); // 'predict' is the function in your Python script
                    dynamic result = predictionModule.get_prediction(filePaths,formPath); // 'predict' is the function in your Python script

                    // Convert the Python result to a C# object
                    string predictionResult = result.ToString();

                    predictionResult = predictionResult.Replace("\"", "'");
                    predictionResult = predictionResult.Replace("{'", "{\"").Replace("':", "\":").Replace(", '", ", \"").Replace("',", "\",")
                        .Replace("'}", "\"}").Replace(": '", ": \"").Replace("\\'","");

                

                    var returnResult = JsonSerializer.Deserialize<PredictionResult>(predictionResult);
                    // Return the prediction as part of your API response

                    
                    List<string> lstfile_paths = new List<string>();
                    foreach (var item in filePaths)
                    {
                        lstfile_paths.Add(item.Replace(".tiff", ".png").Replace("E:\\Mine\\ImageNowFiles\\files\\","http://p-cvda-16rise06.reliance.corp/ImageNow/files/"));
                    }

                    returnResult.file_paths = lstfile_paths;
                    return returnResult;

                }
            }
            catch (Exception)
            {

                throw;
            }


        }
    }
}
