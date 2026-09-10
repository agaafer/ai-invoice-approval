using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class WorkflowQueue
    {
        public string Id { get; set; }
        public string Name { get; set; }

        public int ContainItems { get; set; }

        public string ProcessId{get;set;}
    }
}
