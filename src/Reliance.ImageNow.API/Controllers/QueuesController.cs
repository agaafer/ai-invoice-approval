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
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class QueuesController : ControllerBase
    {
        private readonly AppDbContext _context;

        private readonly ILogger<QueuesController> _logger;
        private readonly AppSettings _appSettings;

        public QueuesController(ILogger<QueuesController> logger, IOptions<AppSettings> appSettings,AppDbContext context)
        {
            _logger = logger;
            _context = context;
            _appSettings = appSettings.Value;

        }

        [HttpGet]
        public IEnumerable<WorkflowQueue> Get()
        {
            List<WorkflowQueue> queues = null;

            List<string> allowedQueues = _appSettings.Queues.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList();
               

            IQueryable<WorkflowQueue> queryable = _context.WorkflowQueues.AsNoTracking();

            //queryable = queryable.Where(p => p.ContainItems > 0 );
            queryable = queryable.Where(p => p.ProcessId == "301YV3Y_000368G6J000012");
            queryable = queryable.OrderBy(p => p.Name);

            queryable = queryable.Where(p => allowedQueues.Any(a => a == p.Name));
            queues = queryable.ToList();
            

       

            return queues;


        }



    }
}
