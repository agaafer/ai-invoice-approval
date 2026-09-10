using Python.Runtime;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Utitlities
{
    public class PythonScriptRunner
    {
        public PythonScriptRunner()
        {
            //    Runtime.PythonDLL = @"C:\Python312\python312.dll"; // I installed the python it this path
            //    PythonEngine.Initialize();
            Runtime.PythonDLL = "C:\\Users\\agaafer\\AppData\\Local\\Programs\\Python\\Python312\\python312.dll";
            PythonEngine.Initialize();
        }
    }
}
