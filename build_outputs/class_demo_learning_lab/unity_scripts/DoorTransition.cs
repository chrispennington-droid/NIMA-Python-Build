using UnityEngine;

// NIMA Phase II Spatial Review Learning Lab - class demo build.
// Attach to a trigger collider that sits in the doorway opening (Door 1 or
// Door 2 in the imported FBX/GLB). On enter, the player either walks through
// (auto) or presses E. The script can teleport the player to a target point
// on the other side of the door if you set "useTeleport".
//
// Recommended setup:
//   - Add an empty GameObject at the door opening, scale a BoxCollider to
//     fit the 6 ft x 8 ft opening, mark it Is Trigger.
//   - Add this script. Set "doorName" to "Door_Lobby_To_ProveOut_Level1" or
//     "Door_Level2_To_ProveOut_Overlook".
//   - Drop a Transform into "exitTarget" if you want a teleport on enter.
public class DoorTransition : MonoBehaviour
{
    [Tooltip("Name of the door for logging. Match the GLB node name.")]
    public string doorName = "Door_Lobby_To_ProveOut_Level1";

    [Tooltip("Tag on the player object. Default = Player.")]
    public string playerTag = "Player";

    [Tooltip("If true, player must press the activation key while inside.")]
    public bool requireKeyPress = false;

    public KeyCode activationKey = KeyCode.E;

    [Tooltip("Optional teleport target. If set, the player is moved here when the door activates.")]
    public Transform exitTarget;

    [Tooltip("Show a brief on-screen prompt while in the trigger.")]
    public bool showPrompt = true;

    private bool playerInside = false;
    private GameObject player;

    private void Reset()
    {
        var col = GetComponent<Collider>();
        if (col != null) col.isTrigger = true;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag(playerTag)) return;
        playerInside = true;
        player = other.gameObject;
        Debug.Log($"[DoorTransition] Player entered trigger for '{doorName}'.");
        if (!requireKeyPress) Activate();
    }

    private void OnTriggerExit(Collider other)
    {
        if (!other.CompareTag(playerTag)) return;
        playerInside = false;
        player = null;
    }

    private void Update()
    {
        if (playerInside && requireKeyPress && Input.GetKeyDown(activationKey))
            Activate();
    }

    private void Activate()
    {
        Debug.Log($"[DoorTransition] '{doorName}' activated.");
        if (exitTarget != null && player != null)
        {
            var cc = player.GetComponent<CharacterController>();
            if (cc != null) cc.enabled = false;
            player.transform.position = exitTarget.position;
            player.transform.rotation = exitTarget.rotation;
            if (cc != null) cc.enabled = true;
        }
    }

    private void OnGUI()
    {
        if (!showPrompt || !playerInside) return;
        string msg = requireKeyPress
            ? $"Press {activationKey} to enter: {doorName.Replace('_', ' ')}"
            : $"Entering: {doorName.Replace('_', ' ')}";
        GUI.Label(new Rect(20, Screen.height - 60, 700, 40), msg);
    }
}
