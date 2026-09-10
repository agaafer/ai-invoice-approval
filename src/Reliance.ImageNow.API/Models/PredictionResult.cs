using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class PredictionResult
    {
        public string file_path { get; set; }

        public List<string> file_paths { get; set; }
       // public string prediction { get; set; }
       public Predication prediction { get; set; }
        public Invoice invoice { get; set; }
    }
}
