using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class BatchPredection
    {
        public long Id { get; set; }
        public string DocumentId { get; set; }
        public string PredictionResult { get; set; }
        public string Name { get; set; }
        public string Percent { get; set; }
       
    }
}
