import { Link } from 'react-router-dom'
import { Moon, Sun, Activity } from 'lucide-react'
import { useTheme } from "../context/ThemeContext";


export default function Navbar() {
    const { light, toggle } = useTheme()

    return (
        <nav className="h-14 flex items-center px-6 border-b-2 border-orange-500 bg-white dark:bg-gray-900">
            <Link to="/" className="flex items-center gap-2 font-bold text-lg text-gray-900 dark:text-white">
                <Activity className="text-orange-500" size={22} />
                MonitorAI
            </Link>
            <div className="ml-auto flex items-center gap-3">
                <Link to="/agents/new" className="px-4 py-1.5 rounded-md text-sm font-medium bg-orange-500 hover:bg-orange-600 text-white transition-colors">
                    + Add Agent
                </Link>
                <button onClick={toggle} className="p-2 rounded-md text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors">
                    {light ? <Moon size={18} /> : <Sun size={18} />}
                </button>
            </div>
        </nav>
    )
}