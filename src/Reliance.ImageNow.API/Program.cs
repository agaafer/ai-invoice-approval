using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Python.Runtime;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API
{
    public class Program
    {
        public static void Main(string[] args)
        {
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                    Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", "C:\\Users\\agaafer\\AppData\\Local\\Programs\\Python\\Python312\\python312.dll");
                    PythonEngine.PythonHome = "C:\\Users\\agaafer\\AppData\\Local\\Programs\\Python\\Python312";
                    PythonEngine.Initialize();
                    PythonEngine.BeginAllowThreads();
                });
    
    }
}
