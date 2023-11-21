using UnityEngine;

public class ScriptHolder<T>
{
    public GameObject gameObject;
    public T script;

    public ScriptHolder(GameObject gameObject, T script)
    {
        this.gameObject = gameObject;
        this.script = script;
    }
}