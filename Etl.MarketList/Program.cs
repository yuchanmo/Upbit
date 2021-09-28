using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using RestSharp;
using RestSharp.Authenticators;

namespace Etl.MarketList
{
    class Program
    {
        static void Main(string[] args)
        {
            var market_url = "https://api.upbit.com/v1/market/all";
            var client = new RestClient(market_url);
            var request = new RestRequest();
            var response = client.Get(request);
            var market_list = JsonConvert.DeserializeObject<List<MarketList>>(response.Content);
            var dc = new CoinStarEntities();
            var existing_rows = dc.MarketList.ToArray();
            var new_rows = market_list.Where(v => !existing_rows.Select(m => m.market).Contains(v.market));
            dc.MarketList.AddRange(new_rows);
            dc.SaveChanges();


        }
    }

    public class MarketDto
    {
        public string market { get; set; }

        public string korean_name { get; set; }

        public string english_name { get; set; }
    }
}
