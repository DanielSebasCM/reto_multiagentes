// Root myDeserializedClass = JsonConvert.DeserializeObject<Root>(myJsonResponse);
using System;
using System.Collections.Generic;

[Serializable]
public class ModelResponse
{
    public int steps;
    public List<Step> data;
}
