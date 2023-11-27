Shader "Custom/Grayscale"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" { }
        _Brightness ("Brightness", Range(0, 1)) = 0.5
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

        CGPROGRAM
        #pragma surface surf Lambert
        
        struct Input
        {
            float2 uv_MainTex;
        };

        sampler2D _MainTex;
        fixed _Brightness;

        void surf(Input IN, inout SurfaceOutput o)
        {
            fixed4 c = tex2D(_MainTex, IN.uv_MainTex);
            float gray = dot(c.rgb, float3(0.299, 0.587, 0.114));
            o.Albedo = gray * _Brightness;
            o.Alpha = c.a;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
