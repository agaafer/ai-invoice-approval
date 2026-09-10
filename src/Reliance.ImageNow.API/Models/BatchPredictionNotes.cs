using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class BatchPredictionNotes
    {
        public int Id { get; set; }
        public string Notes { get; set; }
        public string DocumentId { get; set; }
        public string InvoiceNumber { get; set; }
    }
}
