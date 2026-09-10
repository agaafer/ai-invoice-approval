
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class Instance
    {
        public string Id { get; set; }
        public DateTime? CreatedDateTime { get; set; }

        public ICollection<WorkflowItem> WorkflowItems { get; } = new List<WorkflowItem>();
        public DateTime? ModifiedDateTime { get; set; }
      
        public ICollection<Property> Properties { get; } = new List<Property>();

        public DateTime? APInvoiceDate
        {
            get
            {
                return Properties.FirstOrDefault(s => s.Id == "301YV3X_0005J7FB6000062").Value;
            }
        }
        public DateTime? QueueStartDateTime
        {
            get
            {
                if (WorkflowItems != null && WorkflowItems.Count > 0)
                    return WorkflowItems.FirstOrDefault().WorkflowStartTime;
                else
                    return DateTime.MinValue;
            }
        }
    }

}
