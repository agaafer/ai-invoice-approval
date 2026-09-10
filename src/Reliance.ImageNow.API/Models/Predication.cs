using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class Predication
    {
        public int predicted_class { get; set; }

        public float predicted_probability { get; set; }

        public double percent
        {
            get
            {  
                    return Math.Round(predicted_probability * 100,2);
                
            }
        }
        public string name
        {
            get
            {
                if (predicted_class == 1)
                    return "Accepted";
                else
                    return "Rejected";

            }
        }

    }
}
