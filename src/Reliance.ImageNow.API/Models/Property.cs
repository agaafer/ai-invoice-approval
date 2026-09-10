using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class Property
    {
        public string Id { get; set; }    
   
        public DateTime? Value { get; set; }

        public string InstanceId { get; set; }
    }
}
