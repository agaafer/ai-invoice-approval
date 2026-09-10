using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class WorkflowItem
    {
        public string Id { get; set; }       
        //public string objectId { get; set; }
     
        public string WorkflowQueueId { get; set; }

        public WorkflowQueue WorkflowQueue { get; set; }

        public string InstanceId { get; set; }
        //public string workflowQueueName { get; set; }

        public DateTime? WorkflowStartTime { get; set; }


    }
}
