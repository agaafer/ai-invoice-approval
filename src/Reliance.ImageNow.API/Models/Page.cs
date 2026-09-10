using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class Page
    {
        public string id { get; set; }
        public string name { get; set; }        
        public string extension { get; set; }
        public int pageNumber { get; set; }
    }
}
