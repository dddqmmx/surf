use std::fs;
use std::path::PathBuf;


#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn read_user_profiles(path: String) -> Result<String, String> {
    let path_buf = PathBuf::from(path);
    // 读取文件内容
    match fs::read_to_string(path_buf) {
        Ok(contents) => Ok(contents),
        Err(err) => Err(format!("读取文件时出错: {}", err)),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet,read_user_profiles])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
