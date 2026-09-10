using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class Document
    {
        
        public string Id { get; set; }
        public string VendorID { get; set; }
        public string VendorName { get; set; }
        
        public string InvoiceNumber { get; set; }
        [JsonIgnore]
        public string DocumentTypeId { get; set; }
        [JsonIgnore]
        public string InstanceId { get; set; }
        [JsonIgnore]
        public Instance Instance { get; set; }
        public string Queuename
        {
            get
            {
                if (Instance != null)
                {
                    if (Instance.WorkflowItems != null && Instance.WorkflowItems.Count() > 0)
                    {
                        var WorkflowItem = Instance.WorkflowItems?.FirstOrDefault();
                        if (WorkflowItem != null)
                        {
                            var workflowqueue = WorkflowItem.WorkflowQueue;
                            if (workflowqueue != null)
                                return workflowqueue.Name;
                        }
                    }
                }
                return string.Empty;
            }
        }
        public DateTime? InvoiceDate
        {
            get
            {
                return Instance?.APInvoiceDate;
            }
        }
        public DateTime? CreatedDateTime
        {
            get
            {
                return Instance.CreatedDateTime;
            }
        }
        [JsonIgnore]
        public List<Page> pages { get; set; }

        [NotMapped]
        public string Name { get; set; }

        [NotMapped]
        public string Percent { get; set; }
        [NotMapped]
        public string Notes { get; set; }

    }
}
