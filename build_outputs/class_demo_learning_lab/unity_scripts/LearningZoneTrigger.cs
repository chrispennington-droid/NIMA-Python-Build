using UnityEngine;

// NIMA Phase II Spatial Review Learning Lab - class demo build.
// Attach to a trigger collider placed near each Board_* node (Board_Title,
// Board_Entry, Board_NIMA, Board_RDPark, Board_PhaseII, Board_ProveOut,
// Board_EquipFit, Board_Overlook, Board_QA, Board_Reflection). When the
// player walks into the trigger, the title and body text appear on screen.
//
// The body text is intentionally stored in this component so it survives the
// FBX/GLB round-trip without depending on the importer reading glTF "extras".
// You can pre-populate the text in the Inspector or via a setup script that
// reads the GLB extras at import time.
public class LearningZoneTrigger : MonoBehaviour
{
    [Tooltip("Tag on the player object. Default = Player.")]
    public string playerTag = "Player";

    [Tooltip("Title shown at the top of the popup.")]
    public string title = "Learning Zone";

    [Tooltip("Body text shown below the title.")]
    [TextArea(3, 12)]
    public string body = "";

    [Tooltip("How long the popup stays on screen after entering.")]
    public float displaySeconds = 8.0f;

    [Tooltip("Re-show the popup every time the player enters (otherwise once per session).")]
    public bool retriggerOnReentry = true;

    private float showUntil = 0f;
    private bool shownOnce = false;

    private void Reset()
    {
        var col = GetComponent<Collider>();
        if (col != null) col.isTrigger = true;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag(playerTag)) return;
        if (shownOnce && !retriggerOnReentry) return;
        showUntil = Time.time + displaySeconds;
        shownOnce = true;
        Debug.Log($"[LearningZoneTrigger] {title}");
    }

    private void OnGUI()
    {
        if (Time.time > showUntil) return;
        var pad = 16;
        var w = 520;
        var h = 220;
        var x = Screen.width - w - pad;
        var y = pad;
        GUI.Box(new Rect(x, y, w, h), GUIContent.none);
        var titleStyle = new GUIStyle(GUI.skin.label) { fontSize = 18, fontStyle = FontStyle.Bold, wordWrap = true };
        var bodyStyle  = new GUIStyle(GUI.skin.label) { fontSize = 14, wordWrap = true };
        GUI.Label(new Rect(x + 12, y + 8,  w - 24, 40),  title, titleStyle);
        GUI.Label(new Rect(x + 12, y + 52, w - 24, h - 60), body, bodyStyle);
    }
}
